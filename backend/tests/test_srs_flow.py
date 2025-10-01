import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.main import app
from app.core.database import Base, engine
from app.core import security
from app.models import User, Flashcard
from app.schemas.user import UserCreate
from app.crud import user as user_crud

# --- Cấu hình Test ---

# Tạo một database test riêng biệt
@pytest.fixture(scope="session", autouse=True)
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def get_db_override():
        return db_session
    app.dependency_overrides[security.get_db] = get_db_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# --- Dữ liệu Test ---

@pytest.fixture
def test_user(db_session: Session) -> User:
    """Tạo một user mẫu để test"""
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
        full_name="Test User"
    )
    user = user_crud.user.create(db_session, obj_in=user_in)
    return user

@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Tạo header xác thực cho user test"""
    access_token = security.create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {access_token}"}


# --- Kịch bản Test ---

def test_start_review_session_flow(client: TestClient, db_session: Session, test_user: User, auth_headers: dict):
    """
    Kiểm tra toàn bộ luồng "Start Review Session":
    1. Tạo flashcard mới -> Nó phải "đến hạn" ngay lập tức.
    2. Gọi API /due -> Thẻ mới phải có trong danh sách.
    3. Review thẻ đó -> Ngày ôn tập phải được dời về tương lai.
    4. Gọi lại API /due -> Thẻ đó không còn trong danh sách nữa.
    """

    # --- Giai đoạn 1: Tạo Flashcard và kiểm tra "đến hạn" ---

    # 1.1. Tạo một flashcard mới
    create_response = client.post(
        "/api/v1/flashcards/",
        headers=auth_headers,
        json={"front_text": "Test Word", "back_text": "Test Definition"}
    )
    assert create_response.status_code == 200
    new_card_data = create_response.json()
    new_card_id = new_card_data["id"]

    # Kiểm tra trong DB xem next_review_date có được set hay không
    card_in_db = db_session.query(Flashcard).filter(Flashcard.id == new_card_id).first()
    assert card_in_db is not None
    # Ngày ôn tập phải được set (không phải None)
    assert card_in_db.next_review_date is not None
    # Ngày ôn tập phải gần với thời điểm hiện tại (trong vòng 60 giây)
    time_diff = abs((datetime.utcnow() - card_in_db.next_review_date).total_seconds())
    assert time_diff < 60  # Cho phép chênh lệch tối đa 60 giây

    print(f"\n✅ Giai đoạn 1.1: Tạo thẻ mới thành công (ID: {new_card_id}). Thẻ đến hạn ngay lập tức.")

    # 1.2. Gọi API /due để xem thẻ có trong danh sách không
    due_response_before = client.get("/api/v1/flashcards/due", headers=auth_headers)
    assert due_response_before.status_code == 200
    due_cards_before = due_response_before.json()

    # Thẻ mới tạo phải nằm trong danh sách cần ôn tập
    assert any(card['id'] == new_card_id for card in due_cards_before)

    print("✅ Giai đoạn 1.2: Thẻ mới xuất hiện trong danh sách ôn tập.")

    # --- Giai đoạn 2: Ôn tập và kiểm tra lại ---

    # 2.1. Ôn tập thẻ với đánh giá "Easy" (quality=5)
    review_response = client.post(
        f"/api/v1/flashcards/{new_card_id}/review",
        headers=auth_headers,
        json={"quality": 5}
    )
    assert review_response.status_code == 200
    reviewed_card_data = review_response.json()

    # Ngày ôn tập tiếp theo phải được dời về tương lai
    next_review_date = datetime.fromisoformat(reviewed_card_data["next_review_date"].replace('Z', '+00:00'))
    # Với quality=5 (Easy), interval sẽ là 6 ngày theo thuật toán SM-2
    assert next_review_date > datetime.utcnow() + timedelta(days=5)

    print(f"✅ Giai đoạn 2.1: Ôn tập thẻ thành công. Lịch ôn tập mới: {next_review_date.strftime('%Y-%m-%d')}.")

    # 2.2. Gọi lại API /due. Thẻ vừa ôn tập không được xuất hiện nữa.
    due_response_after = client.get("/api/v1/flashcards/due", headers=auth_headers)
    assert due_response_after.status_code == 200
    due_cards_after = due_response_after.json()

    # Thẻ vừa ôn tập KHÔNG được nằm trong danh sách
    assert not any(card['id'] == new_card_id for card in due_cards_after)

    print("✅ Giai đoạn 2.2: Thẻ đã ôn tập không còn trong danh sách ôn tập nữa.")
    print("\n🎉 Toàn bộ luồng 'Start Review Session' hoạt động chính xác!")

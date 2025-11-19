import { useEffect, useState } from "react";
import { useNotificationStore } from "../store/useNotificationStore";
import { useAuthStore } from "../store/authStore";

export default function NotificationsPage() {
  const { user } = useAuthStore();
  const { notifications, fetchNotifications, markAsRead } =
    useNotificationStore();
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    if (user) {
      console.log("Fetching notifications for user:", user.id);
      fetchNotifications();
    }
  }, [user]);

  const handleSelectNotification = async (id: number) => {
    setSelectedId(id);
    await markAsRead(id);
  };

  const selectedNotif = notifications.find((n) => n.id === selectedId);

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6 h-[calc(100vh-100px)]">
      {/* LEFT COLUMN */}
      <div className="border rounded-lg shadow-sm bg-white flex flex-col">
        <div className="p-4 font-semibold border-b">Tất cả thông báo</div>
        <div className="overflow-y-auto">
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                selectedId === n.id ? "bg-blue-50" : ""
              } ${!n.isRead ? "font-bold" : "font-normal"}`}
              onClick={() => handleSelectNotification(n.id)}
            >
              <div className="flex justify-between items-center">
                <p className="truncate">{n.title}</p>
                {!n.isRead && (
                  <span className="ml-2 w-2.5 h-2.5 bg-primary rounded-full flex-shrink-0" />
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">{n.time}</p>
            </div>
          ))}
        </div>
      </div>

      {/* RIGHT COLUMN */}
      <div className="md:col-span-2 border rounded-lg shadow-sm bg-white p-6">
        {selectedNotif ? (
          <>
            <h2 className="text-2xl font-bold mb-3">{selectedNotif.title}</h2>
            <p className="text-sm text-gray-500 mb-4">{selectedNotif.time}</p>
            <div className="prose max-w-none">
              <p>{selectedNotif.body}</p>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">
              Hãy chọn 1 thông báo để xem chi tiết.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

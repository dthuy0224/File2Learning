# System Review – 17 Nov 2025

This document captures the current logic review and next-step proposals for the **Adaptive Learning Loop**, **Document Processing**, **AI services**, and **progress state management**. All observations are derived from the latest code state.

---

## 1. Adaptive Learning Loop

### Current Flow (based on code)
1. **Quiz completion**
   - Frontend `QuizResultPage.tsx` posts results via `quizService.submitQuizAttempt`.
   - Backend `quizzes.py` stores attempt data; `analytics.py` exposes read-only stats (`/users/me/...`).

2. **Recommendations**
   - `recommendation_engine.py` can be invoked manually (`POST /recommendations/generate`) or indirectly when `DailyPlanGenerator` notices no fresh recommendations (see `plan_generator.py` lines 54–83).

3. **Daily plan generation**
   - `GET /plans/today` (`daily_plans.py:get_today_plan`) either returns today’s plan or invokes `generate_daily_plan`.
   - Generator pulls:
     - Due flashcards, weak topics, active goals (CRUD calls).
     - Active recommendations (`crud_recommendation.get_active_recommendations`).
     - Active schedule (via `crud_study_schedule.get_active_schedule`).

4. **Schedule adjustments**
   - Currently **manual**: `/schedules/{id}/adjust` calls `schedule_adjuster.py`.
   - Adjuster analyzes adherence, overload, missed days, and updates `schedule.schedule_config.daily_minutes`.

5. **Today’s Plan consumption**
   - `TodayPlanPage.tsx` fetches `/plans/today` and renders tasks.

### Gaps & Risks
- **Trigger clarity**: No automatic hook ties quiz completion to recommendation generation or schedule adjustment. Everything happens lazily when `/plans/today` is called or when a user presses “Auto-adjust”.
- **Potential race**: `DailyPlanGenerator` and `ScheduleAdjuster` operate independently. If adjuster increases daily load while a new plan is being generated, there is no guarantee of consistent ordering.
- **Analytics lag**: Dashboard hooks (`useProgress.ts`) rely on React Query refetch intervals; no invalidation occurs after quiz submission.

### Recommendations
1. **Document flow** (for dev & ops)
   - Add a sequence diagram in `docs/` showing: Quiz submission → analytics update → (optional Celery job) recommendation regeneration → plan generation.
2. **Introduce triggers**
   - Option A: After quiz submission succeeds, enqueue a Celery task (`update_user_learning_state`) that:
     1. Updates analytics cache.
     2. Regenerates recommendations (with throttling).
     3. Flags schedule for adjustment (set `needs_adjustment=True`).
   - Option B: Nightly job that recomputes everything; TodayPlan fetch uses `needs_adjustment` flags to refresh.
3. **Order of operations**
   - Define: `ScheduleAdjuster` runs before `DailyPlanGenerator` on a given day. E.g., `/plans/today` can internally check `schedule.needs_adjustment` and invoke adjuster once before generating tasks.

---

## 2. Async Document Processing

### Current Pipeline
1. Upload endpoint stores file + metadata, sets `processing_status='pending'`.
2. Celery task `process_document_task` (single monolithic job):
   - Extracts text, cleans content, extracts metadata.
   - Updates document rows (`content`, `word_count`, `difficulty_level`, `processing_status='completed'`).
   - On failure: sets `processing_status='failed'`, stores error.

3. Additional AI features (summary, vocab, quiz) are triggered from other endpoints (`ai.py`):
   - `/ai/{document_id}/generate-quiz`
   - `/ai/{document_id}/generate-flashcards`
   - `/ai/{document_id}/generate-summary`
   - Each call is synchronous (per HTTP request).

### Gaps
- **No partial successes**: If summary succeeds but quiz generation fails, there’s no per-artifact status; everything relies on manual retries.
- **Blocking UX**: Generating quiz/flashcards per request can take several seconds and ties up the HTTP request.
- **Status flags exist (`document.processing_status`, `processing_error`, `key_vocabulary`) but aren’t granular.**

### Recommendations
1. **Task chaining**
   - Break Celery work into explicit tasks:
     1. `extract_text_task` – current file extraction + metadata.
     2. `generate_summary_task`
     3. `generate_key_vocab_task`
     4. `generate_quiz_task`
   - Use Celery chains/chords so that failure in later tasks doesn’t nullify previous outputs.
2. **Document schema update**
   - Add columns like `summary_status`, `quiz_status`, `flashcard_status` with timestamps. Alembic migration already indicates readiness (e.g., `key_vocabulary` column).
3. **Frontend tracking**
   - Extend `useDocumentStatus` hook to show per-artifact progress (Summary ready, Quiz pending, etc.).

---

## 3. Multi-AI Service Refactor Plan

### Current State
- `backend/app/services/multi_ai_service.py` (~600 lines) handles:
  - Provider bootstrapping (Gemini, Groq).
  - Quiz generation, flashcards, key vocabulary, summary, chat responses.
  - Prompt building, response parsing, fallback logic, provider stats.

### Issues
- Violates Single Responsibility Principle; every touch to prompts or parsing happens in one file.
- Hard to test: no clear seams to inject custom prompt logic or unit test parsing.
- Logging and error handling duplicated across functions.

### Refactor Proposal
1. **Directory structure**
   ```
   backend/app/services/ai/
     __init__.py
     base_client.py          # handles provider routing
     quiz_generation.py
     flashcard_generation.py
     vocabulary_extraction.py
     summarization.py
     chat_service.py
   ```

2. **Facade**
   - Keep `multi_ai_service.py` as a thin facade exposing the old public API (generate_quiz, …) but delegate to module-specific classes.

3. **Prompt + parser encapsulation**
   - Each module defines `build_prompt()`, `parse_response()`, and uses a common `AIClient` class for provider routing.

4. **Benefits**
   - Easier to update prompts without risking other features.
   - Potential to plug new providers or fallback heuristics per use case.
   - Unit testing of parser logic becomes straightforward.

---

## 4. Frontend State & Invalidation

### Findings
- Global auth handled via Zustand `authStore.ts`.
- Progress-related data uses React Query hooks (`useProgress.ts`) with set `refetchInterval`/`staleTime`.
- After quiz submission or flashcard review, we do **not** invalidate progress queries programmatically; dashboards rely on periodic refetch.
- TodayPlan (`TodayPlanPage.tsx`) invalidates `['todayPlan']` when start/skip/complete plan, but Dashboard’s KPI widgets (streak, accuracy) refresh only on interval/focus.

### Recommendations
1. **React Query invalidations**
   - After quiz submission or flashcard review, call `queryClient.invalidateQueries` for:
     - `['userStats']`
     - `['activityHeatmap']`
     - `['recentActivities']`
   - This ensures Dashboard reflects new data immediately.

2. **Optional Zustand store**
   - Introduce `useProgressStore` to cache core KPIs (streak, mastery). Queries update the store; multiple pages consume consistent values even without rerender.

3. **Shared hooks for Today Plan + Dashboard**
   - Example: `useTodayPlan()` hook that centralizes `['todayPlan']` query, so both Dashboard and StudySchedule page can read the same cache instead of separate fetches.

---

## Next Steps Checklist
1. **Document** the adaptive learning flow diagrammatically for developers.
2. **Decide** on real-time vs nightly triggers and implement Celery task(s) accordingly.
3. **Design** the Celery task chain for document processing and extend document status schema.
4. **Break down** `multi_ai_service` into module-specific services.
5. **Add** React Query invalidation in quiz/flashcard flows; consider shared Zustand store for KPIs.

These actions will make the adaptive learning experience more responsive, improve observability of document processing, and keep the AI layer maintainable as we add new features.


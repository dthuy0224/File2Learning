// src/store/useNotificationStore.ts
import { create } from "zustand";
import api from "../services/api";

export interface Notification {
  id: number;
  title: string;
  body: string;
  time: string;
  isRead: boolean;
}

interface NotificationStore {
  notifications: Notification[];
  fetchNotifications: () => Promise<void>;
  markAsRead: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
}

export const useNotificationStore = create<NotificationStore>((set, get) => ({
  notifications: [],

  fetchNotifications: async () => {
    try {
      const userId = localStorage.getItem("user-id");
      if (!userId) {
        console.warn("No user-id in localStorage, skipping fetchNotifications");
        set({ notifications: [] });
        return;
      }

      console.log("Fetching notifications for user:", userId);

      // Chỉ gọi /notifications vì baseURL + proxy sẽ rewrite sang backend /api/v1/notifications
      const res = await api.get(`/notifications/${userId}`);

      const mapped = res.data.map((n: any) => ({
        id: n.id,
        title: n.title,
        body: n.body,
        time: n.created_at,
        isRead: n.is_read,
      }));

      set({ notifications: mapped });
      console.log("Fetched notifications:", mapped);
    } catch (err) {
      console.error("Failed to fetch notifications", err);
      set({ notifications: [] });
    }
  },

  markAsRead: async (id: number) => {
    try {
      await api.post(`/notifications/${id}/read`);
      set({
        notifications: get().notifications.map((n) =>
          n.id === id ? { ...n, isRead: true } : n
        ),
      });
      console.log("Marked notification as read:", id);
    } catch (err) {
      console.error("Failed to mark as read", err);
    }
  },

  markAllAsRead: async () => {
    try {
      const userId = localStorage.getItem("user-id");
      if (!userId) {
        console.warn("No user-id in localStorage, skipping markAllAsRead");
        return;
      }

      await api.post(`/notifications/read-all/${userId}`);
      set({
        notifications: get().notifications.map((n) => ({ ...n, isRead: true })),
      });
      console.log("Marked all notifications as read for user:", userId);
    } catch (err) {
      console.error("Failed to mark all as read", err);
    }
  },
}));

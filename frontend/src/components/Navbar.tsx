import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { BookOpen, User, LogOut, Bell } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { useNotificationStore } from "../store/useNotificationStore";

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const notifRef = useRef<HTMLDivElement | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);

  const { notifications, fetchNotifications, markAsRead, markAllAsRead } =
    useNotificationStore();

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  useEffect(() => {
    if (user) fetchNotifications();
  }, [user, fetchNotifications]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        notifRef.current &&
        !notifRef.current.contains(e.target as Node) &&
        menuRef.current &&
        !menuRef.current.contains(e.target as Node)
      ) {
        setIsNotifOpen(false);
        setIsMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleClickNotification = async (id: number) => {
    await markAsRead(id);
  };

  const handleMarkAllAsRead = async () => {
    if (user) await markAllAsRead();
  };

  const handleGoToNotificationsPage = () => {
    setIsNotifOpen(false);
    navigate("/notifications");
  };

  const toggleNotif = () => {
    setIsNotifOpen((prev) => !prev);
    setIsMenuOpen(false);
  };

  const toggleMenu = () => {
    setIsMenuOpen((prev) => !prev);
    setIsNotifOpen(false);
  };

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex justify-between items-center">
        <Link to="/dashboard" className="flex items-center space-x-2">
          <BookOpen className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold text-gray-900">
            File2Learning
          </span>
        </Link>

        <div className="flex items-center space-x-6">
          {/* Notification */}
          <div className="relative" ref={notifRef}>
            <button
              onClick={toggleNotif}
              className="p-2 rounded-full hover:bg-gray-100 relative"
            >
              <Bell className="h-5 w-5 text-gray-600" />
              {unreadCount > 0 && (
                <span className="absolute top-0.5 right-0.5 flex items-center justify-center w-5 h-5 bg-red-600 text-white text-xs font-bold rounded-full">
                  {unreadCount}
                </span>
              )}
            </button>

            {isNotifOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-md shadow-lg z-20">
                <div className="px-4 py-2 font-semibold border-b text-gray-700 flex items-center justify-between">
                  <span>Notifications</span>
                  <button
                    onClick={handleMarkAllAsRead}
                    className="text-xs text-primary hover:underline"
                  >
                    Mark all as read
                  </button>
                </div>

                {notifications.length > 0 ? (
                  <div className="max-h-72 overflow-y-auto">
                    {notifications.map((notif) => (
                      <div
                        key={notif.id}
                        onClick={() => handleClickNotification(notif.id)}
                        className={`px-4 py-3 border-b transition cursor-pointer flex flex-col ${
                          notif.isRead
                            ? "bg-white hover:bg-gray-50"
                            : "bg-gray-50 hover:bg-gray-100"
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <p
                            className={`text-sm ${
                              notif.isRead
                                ? "text-gray-800"
                                : "text-gray-900 font-semibold"
                            }`}
                          >
                            {notif.title}
                          </p>
                          {!notif.isRead && (
                            <span className="ml-2 inline-block w-2 h-2 bg-primary rounded-full" />
                          )}
                        </div>
                        <p
                          className={`text-xs truncate mt-1 ${
                            notif.isRead ? "text-gray-500" : "text-gray-600"
                          }`}
                        >
                          {notif.body}
                        </p>
                        <p className="text-xs text-primary mt-1">
                          {notif.time}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 text-sm text-gray-500">
                    Không có thông báo
                  </div>
                )}

                <div className="border-t">
                  <button
                    onClick={handleGoToNotificationsPage}
                    className="block w-full text-center px-4 py-2 text-sm font-medium text-primary hover:bg-gray-100 transition"
                  >
                    See All Notifications
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* User menu */}
          <div className="relative" ref={menuRef}>
            <button
              onClick={toggleMenu}
              className="flex items-center space-x-2 hover:bg-gray-100 px-3 py-2 rounded-lg transition"
            >
              <User className="h-5 w-5 text-gray-600" />
              <span className="text-sm text-gray-700">
                {user?.full_name || user?.username}
              </span>
            </button>

            {isMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-md shadow-lg z-20">
                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    navigate("/profile");
                  }}
                  className="w-full flex items-center space-x-2 px-4 py-2 hover:bg-gray-100 text-left"
                >
                  <User className="h-4 w-4" />
                  <span>Edit Profile</span>
                </button>
                <button
                  onClick={() => {
                    logout();
                    setIsMenuOpen(false);
                  }}
                  className="w-full flex items-center space-x-2 px-4 py-2 hover:bg-gray-100 text-left"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

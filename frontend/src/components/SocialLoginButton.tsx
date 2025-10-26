import { useState } from "react";
import { Button } from "./ui/button";
import { useAuthStore } from "../store/authStore";
import toast from "react-hot-toast";

interface SocialLoginButtonProps {
  provider: "google" | "microsoft" | "github";
  onSuccess: (token: string, user: any) => void;
  onError: (error: string) => void;
  disabled?: boolean;
}

export default function SocialLoginButton({
  provider,
  onSuccess,
  onError,
  disabled = false,
}: SocialLoginButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuthStore();

  const API_BASE_URL =
    import.meta.env.VITE_API_URL || "http://localhost:8000"; // cấu hình API backend

  const providerConfig = {
    google: {
      name: "Google",
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24">
          <path
            fill="currentColor"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="currentColor"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="currentColor"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
          />
          <path
            fill="currentColor"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
          />
        </svg>
      ),
      color: "bg-red-600 hover:bg-red-700",
      text: "Continue with Google",
    },
    microsoft: {
      name: "Microsoft",
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24">
          <path
            fill="currentColor"
            d="M1 1h10v10H1V1zm12 0h10v10H13V1zM1 13h10v10H1v-10zm12 0h10v10H13v-10z"
          />
        </svg>
      ),
      color: "bg-blue-600 hover:bg-blue-700",
      text: "Continue with Microsoft",
    },
    github: {
      name: "GitHub",
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24">
          <path
            fill="currentColor"
            d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
          />
        </svg>
      ),
      color: "bg-gray-900 hover:bg-gray-800",
      text: "Continue with GitHub",
    },
  };

  const config = providerConfig[provider];

  const handleSocialLogin = async () => {
    if (disabled || isLoading) return;

    setIsLoading(true);
    try {
      // gọi backend API để lấy OAuth URL
      const response = await fetch(
        `${API_BASE_URL}/api/v1/auth/oauth/${provider}`
      );
      if (!response.ok) {
        throw new Error("Failed to get OAuth URL");
      }

      const { authorization_url } = await response.json();

      // redirect sang provider
      window.location.href = authorization_url;
    } catch (error: any) {
      console.error("Social login error:", error);
      toast.error("Failed to start social login");
      onError(error.message || "Social login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      type="button"
      variant="outline"
      onClick={handleSocialLogin}
      disabled={disabled || isLoading}
      className={`w-full justify-center ${config.color} text-white border-0`}
    >
      {isLoading ? (
        <svg
          className="animate-spin -ml-1 mr-3 h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      ) : (
        config.icon
      )}
      {isLoading ? "Connecting..." : config.text}
    </Button>
  );
}

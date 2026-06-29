def restart_vpn_service(user_id: str) -> str:
    """Simulates restarting a user's VPN session - a safe, reversible action."""
    return f"VPN session reset for {user_id}. User should reconnect within 30 seconds."


def reset_password(user_id: str) -> str:
    """Simulates an AD password reset - safe, reversible, audit-logged in real systems."""
    return f"Password reset for {user_id}. Temporary password sent to registered mobile."
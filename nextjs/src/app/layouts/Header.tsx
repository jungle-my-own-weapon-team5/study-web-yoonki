"use client";

import Link from "next/link";
import { useEffect } from "react";

import { useAuthStore } from "@/stores/auth";
const Header = () => {
  const { user, isLoading, checkAuth, logout } = useAuthStore();

  useEffect(() => {
    void checkAuth();
  }, [checkAuth]);

  return (
    <header className="flex justify-evenly">
      <Link href="/">Main</Link>
      {isLoading ? null : user ? (
        <>
          <span>{user.nickname}</span>
          <button className="cursor-pointer" type="button" onClick={logout}>
            Logout
          </button>
        </>
      ) : (
        <>
          <Link href="/auth/login">Login</Link>
          <Link href="/auth/register">Register</Link>
        </>
      )}
    </header>
  );
};

export default Header;

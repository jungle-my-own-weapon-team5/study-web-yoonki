"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/config";

type CurrentUser = {
  id: number;
  email: string;
  nickname: string;
};

const Header = () => {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/auth/user`, {
      credentials: "include",
    })
      .then((response) => {
        if (!response.ok) {
          return null;
        }
        return response.json();
      })
      .then((data: CurrentUser | null) => {
        setUser(data);
      })
      .catch(() => {
        setUser(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const handleLogout = async () => {
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    setUser(null);
  };

  return (
    <header className="flex justify-evenly">
      <Link href="/">Main</Link>
      {isLoading ? null : user ? (
        <>
          <span>{user.nickname}</span>
          <button className="cursor-pointer" type="button" onClick={handleLogout}>
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

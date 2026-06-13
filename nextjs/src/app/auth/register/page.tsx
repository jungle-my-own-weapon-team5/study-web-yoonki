"use client";

import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { register } from "@/lib/auth-api";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "next/navigation";
import { useState } from "react";

const RegisterPage = () => {

    const router = useRouter();
    const setUser = useAuthStore((state) => state.setUser);

    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setErrorMessage('');
        setIsSubmitting(true);

        try {
            const user = await register({
                email,
                nickname: name,
                password,
            });
            setUser(user);
            router.push("/");
        } catch (error) {
            setErrorMessage(error instanceof Error ? error.message : "Register failed.");
        } finally {
            setIsSubmitting(false);
        }
        
    };

    return <>
        <div className="flex min-h-[70vh] items-center justify-center px-6 py-12">
            <Card className="w-full max-w-sm text-left">
                <CardHeader>
                    <CardTitle className="text-3xl">Register</CardTitle>
                    <CardDescription>Create a new account.</CardDescription>
                </CardHeader>

                <CardContent>
                <form className="space-y-5" onSubmit={onSubmit}>
                    <div className="flex flex-col gap-2">
                        <Label htmlFor="name">Name</Label>
                        <Input
                            id="name"
                            type="text"
                            value={name}
                            onChange={e => setName(e.target.value)}
                        />
                    </div>

                    <div className="flex flex-col gap-2">
                        <Label htmlFor="email">Email</Label>
                        <Input
                            id="email"
                            type="email"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                        />
                    </div>

                    <div className="flex flex-col gap-2">
                        <Label htmlFor="password">Password</Label>
                        <Input
                            id="password"
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                        />
                    </div>

                    <div className="flex flex-col gap-2">
                        <Label htmlFor="confirm-password">Confirm Password</Label>
                        <Input
                            id="confirm-password"
                            type="password"
                            value={confirmPassword}
                            onChange={e => setConfirmPassword(e.target.value)}
                        />
                    </div>

                    {errorMessage && (
                        <p className="text-sm text-red-600">{errorMessage}</p>
                    )}

                    <Button
                        className="mt-2 w-full"
                        size="lg"
                        type="submit"
                        disabled={!name || !email || !password || !confirmPassword || isSubmitting}
                    >
                        {isSubmitting ? "Wait for register...":"Register"}
                    </Button>
                </form>
                </CardContent>
            </Card>
        </div>
    </>
}

export default RegisterPage;

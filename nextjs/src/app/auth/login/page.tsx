'use client';
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
import { login } from "@/lib/auth-api";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "next/navigation";
import { useState } from "react";

const LoginPage = () => {

    const router = useRouter();
    const setUser = useAuthStore((state) => state.setUser);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setErrorMessage('');
        setIsSubmitting(true);

        try {
            const user = await login({ email, password });
            setUser(user);
            router.push("/");
        } catch (error) {
            setErrorMessage(error instanceof Error ? error.message : "Login failed");
        } finally {
            setIsSubmitting(false);
        }
    };

    return <>
        <div className="flex min-h-[70vh] items-center justify-center px-6 py-12">
            <Card className="w-full max-w-sm text-left">
                <CardHeader>
                    <CardTitle className="text-3xl">Login</CardTitle>
                    <CardDescription>Enter your account information.</CardDescription>
                </CardHeader>

                <CardContent>
                <form className="space-y-5" onSubmit={onSubmit}>
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

                    {errorMessage && (
                        <p className="text-sm text-red-600">{errorMessage}</p>
                    )}

                    <Button
                        className="mt-2 w-full"
                        size="lg"
                        type="submit"
                        disabled={!email || !password || isSubmitting}
                    >
                        {isSubmitting ? "Logging in..." : "Login"}
                    </Button>
                </form>
                </CardContent>
            </Card>
        </div>
    </>
}

export default LoginPage;

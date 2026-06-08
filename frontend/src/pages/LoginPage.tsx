import { useState } from "react";
import Layout from "../layouts/Layout"

const LoginPage = () => {

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    return <Layout>
        <div className="flex min-h-[70vh] items-center justify-center px-6 py-12">
            <div className="w-full max-w-sm rounded-lg border border-gray-200 bg-white px-8 py-10 text-left shadow-sm">
                <div className="mb-8">
                    <h1 className="mb-2 text-3xl font-semibold text-gray-950">Login</h1>
                    <p className="text-sm text-gray-500">Enter your account information.</p>
                </div>

                <form className="space-y-5">
                    <div className="flex flex-col gap-2">
                        <label className="text-sm font-medium text-gray-700" htmlFor="email">Email</label>
                        <input
                            id="email"
                            className="h-11 rounded-md border border-gray-300 px-3 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                            type="email"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                        />
                    </div>

                    <div className="flex flex-col gap-2">
                        <label className="text-sm font-medium text-gray-700" htmlFor="password">Password</label>
                        <input
                            id="password"
                            className="h-11 rounded-md border border-gray-300 px-3 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                        />
                    </div>

                    <button
                        className="mt-2 h-11 w-full rounded-md bg-gray-950 text-sm font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-300"
                        type="submit"
                        disabled={!email || !password}
                    >
                        Login
                    </button>
                </form>
            </div>
        </div>
    </Layout>
}

export default LoginPage;

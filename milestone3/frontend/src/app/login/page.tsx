"use client";

import { FormEvent } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Droplets, Sprout } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    router.push("/");
  }

  return (
    <main className="min-h-screen grid lg:grid-cols-[1fr_1fr] bg-white">
      <section className="flex flex-col px-6 py-8 sm:px-12 lg:px-16 xl:px-24">
        <a href="/" className="inline-flex items-center gap-3 self-start text-farm-dark">
          <span className="grid h-11 w-11 place-items-center rounded-xl bg-farm-primary text-white">
            <Sprout className="h-6 w-6" aria-hidden="true" />
          </span>
          <span className="text-lg font-extrabold">Fieldwise</span>
        </a>

        <div className="my-auto w-full max-w-md py-12 mx-auto">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-farm-emerald">Farmer workspace</p>
          <h1 className="mt-3 text-3xl sm:text-4xl font-extrabold text-gray-950">Welcome back</h1>
          <p className="mt-2 text-sm leading-6 text-gray-600">Sign in to check your fields and irrigation plan.</p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <label className="block text-sm font-semibold text-gray-800">
              Email address
              <input
                name="email"
                type="email"
                autoComplete="email"
                required
                placeholder="you@example.com"
                className="mt-2 block h-12 w-full rounded-lg border border-gray-300 bg-white px-3.5 text-sm font-normal text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-farm-emerald focus:ring-2 focus:ring-farm-emerald/20"
              />
            </label>
            <label className="block text-sm font-semibold text-gray-800">
              Password
              <input
                name="password"
                type="password"
                autoComplete="current-password"
                required
                placeholder="Enter your password"
                className="mt-2 block h-12 w-full rounded-lg border border-gray-300 bg-white px-3.5 text-sm font-normal text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-farm-emerald focus:ring-2 focus:ring-farm-emerald/20"
              />
            </label>
            <button
              type="submit"
              className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-farm-primary px-4 text-sm font-bold text-white transition hover:bg-farm-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-farm-primary"
            >
              Enter demo workspace
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </button>
          </form>

          <p className="mt-5 rounded-lg border border-amber-200 bg-amber-50 px-3.5 py-3 text-xs leading-5 text-amber-950">
            Demo access only. This project does not yet verify accounts or passwords.
          </p>
        </div>

        <p className="text-xs text-gray-500">Smart Irrigation Assistant</p>
      </section>

      <aside className="relative hidden min-h-screen overflow-hidden bg-farm-dark lg:block">
        <img
          src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=85"
          alt="Green agricultural fields beneath a wide open sky"
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-black/35" />
        <div className="absolute inset-x-0 bottom-0 p-12 xl:p-16 text-white">
          <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-white/35 bg-white/15 backdrop-blur-sm">
            <Droplets className="h-6 w-6" aria-hidden="true" />
          </div>
          <p className="text-sm font-semibold text-white/80">Grow with confidence</p>
          <h2 className="mt-2 max-w-xl text-3xl xl:text-4xl font-extrabold leading-tight">
            Better irrigation starts with a clearer view of your fields.
          </h2>
        </div>
      </aside>
    </main>
  );
}
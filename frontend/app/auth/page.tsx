import { redirect } from "next/navigation";

type AuthPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function AuthPage({ searchParams }: AuthPageProps) {
  const params = await searchParams;
  const nextParams = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (typeof value === "string") {
      nextParams.set(key, value);
    } else if (Array.isArray(value)) {
      value.forEach((entry) => nextParams.append(key, entry));
    }
  }

  const query = nextParams.toString();
  redirect(query ? `/login.html?${query}` : "/login.html");
}


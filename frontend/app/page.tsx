import type { Metadata } from "next";
import { HomeLanding } from "@/components/boostai/HomeLanding";

export const metadata: Metadata = {
  title: "BoostAI",
  description:
    "Choose the BoostAI route for school or university and preview the study workspace directly on the main page."
};

export default function Page() {
  return <HomeLanding />;
}


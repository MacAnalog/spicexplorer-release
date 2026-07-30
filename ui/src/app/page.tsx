import { redirect } from "next/navigation";

/** Root → default Studio view. All real views live under the (studio) group. */
export default function Home() {
  redirect("/setup");
}

import { permanentRedirect } from "next/navigation";

// Eski manzil (/kategoriya/{slug}) -> yangi toza manzil (/{slug}) 301 redirect.
export default async function LegacyCategoryRedirect({ params }) {
  const { slug } = await params;
  permanentRedirect(`/${slug}`);
}

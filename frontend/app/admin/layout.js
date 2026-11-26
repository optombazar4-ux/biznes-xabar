export const metadata = {
  title: "Admin panel",
  robots: { index: false, follow: false },
  alternates: { canonical: "/admin" },
};

export default function AdminLayout({ children }) {
  return children;
}

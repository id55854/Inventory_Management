export default function StoreDetailPage({ params }: { params: { storeId: string } }) {
  return (
    <main style={{ padding: "2rem" }}>
      Store {params.storeId} — detail (placeholder).
    </main>
  );
}

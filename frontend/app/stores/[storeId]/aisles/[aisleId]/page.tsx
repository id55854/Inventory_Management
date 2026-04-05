export default function AislePage({
  params,
}: {
  params: { storeId: string; aisleId: string };
}) {
  return (
    <main style={{ padding: "2rem" }}>
      Store {params.storeId} — Aisle {params.aisleId} (placeholder).
    </main>
  );
}

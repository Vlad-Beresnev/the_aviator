export default async function GamePage({
  params,
}: {
  params: Promise<{ ident: string }>;
}) {
  const { ident } = await params;
  return <main><h1>Game: {ident}</h1></main>;
}

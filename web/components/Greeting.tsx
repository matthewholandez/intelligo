import { greeting } from "@/lib/mock";

export function Greeting() {
  return (
    <>
      <h1 className="greeting">{greeting.headline}</h1>
      <p className="greeting__sub">{greeting.sub}</p>
    </>
  );
}

type Variant = "scene" | "end" | "footnote";

const glyph: Record<Variant, string> = {
  scene: "❦",
  end: "☙",
  footnote: "§",
};

export function Fleuron({ variant = "scene" }: { variant?: Variant }) {
  if (variant === "end") {
    return (
      <div className="end-mark" aria-hidden="true">
        {glyph.end}
      </div>
    );
  }
  return <div className="fleuron">{glyph[variant]}</div>;
}

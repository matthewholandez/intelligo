import Link from "next/link";
import { cn } from "@/lib/utils";

type AppShellProps = {
  children: React.ReactNode;
  width?: "default" | "reading" | "wide";
  headerRight?: React.ReactNode;
  hideHeader?: boolean;
};

const widthClasses = {
  default: "max-w-[1100px]",
  reading: "max-w-[680px]",
  wide: "max-w-[1100px]",
};

export function AppShell({
  children,
  width = "default",
  headerRight,
  hideHeader = false,
}: AppShellProps) {
  return (
    <div className="min-h-screen flex flex-col">
      {!hideHeader && (
        <header className="border-b border-border bg-background">
          <div
            className={cn(
              "mx-auto flex h-14 items-center justify-between px-4 sm:px-6",
              widthClasses.default
            )}
          >
            <Link
              href="/"
              className="text-base font-semibold text-foreground transition-colors duration-150 hover:text-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              Intelligo
            </Link>
            {headerRight ? <div className="flex items-center gap-2">{headerRight}</div> : null}
          </div>
        </header>
      )}
      <main
        className={cn(
          "mx-auto w-full flex-1 px-4 py-8 sm:px-6",
          widthClasses[width]
        )}
      >
        {children}
      </main>
    </div>
  );
}

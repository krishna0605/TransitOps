"use client";

export default function GlobalError({ reset }: { reset: () => void }) {
  return (
    <html lang="en">
      <body>
        <main className="grid min-h-screen place-items-center px-6 text-center">
          <div>
            <h1>TransitOps encountered an unexpected error.</h1>
            <button onClick={reset} type="button">
              Reload application
            </button>
          </div>
        </main>
      </body>
    </html>
  );
}

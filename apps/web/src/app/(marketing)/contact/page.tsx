import type { Metadata } from "next";
import { Clock, Mail, MapPin } from "lucide-react";

import { ContactForm } from "@/components/marketing/contact-form";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Contact",
  description: "Get in touch with the TransitOps team.",
};

const DETAILS = [
  { icon: Mail, label: "Email", value: "hello@transitops.example" },
  { icon: MapPin, label: "Location", value: "Gandhinagar, Gujarat" },
  { icon: Clock, label: "Hours", value: "Mon–Fri, 9:00–18:00 IST" },
];

export default function ContactPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-16 lg:px-8">
      <div className="max-w-2xl">
        <p className="text-sm font-medium text-brand">Contact</p>
        <h1 className="mt-2 text-4xl font-bold tracking-tight sm:text-5xl">
          Talk to the team
        </h1>
        <p className="mt-4 text-lg leading-8 text-muted-foreground">
          Questions about TransitOps or want a walkthrough? Send us a note and
          we&apos;ll respond soon.
        </p>
      </div>

      <div className="mt-12 grid gap-8 lg:grid-cols-[1fr_0.6fr]">
        <Card>
          <CardHeader>
            <CardTitle>Send a message</CardTitle>
          </CardHeader>
          <CardContent>
            <ContactForm />
          </CardContent>
        </Card>

        <div className="space-y-4">
          {DETAILS.map((detail) => (
            <div key={detail.label} className="flex items-start gap-3">
              <div className="grid size-10 shrink-0 place-items-center rounded-lg bg-brand/10 text-brand">
                <detail.icon className="size-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{detail.label}</p>
                <p className="font-medium">{detail.value}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

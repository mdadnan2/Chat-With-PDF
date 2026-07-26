"use client";

import Link from "next/link";
import { FileText, Upload, CheckCircle2, Calendar } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { formatFileSize } from "@/lib/utils";
import type { DocumentInfo } from "@/types";

interface DocumentCardProps {
  document: DocumentInfo;
}

export function DocumentCard({ document }: DocumentCardProps) {
  const uploadDate = new Date(document.uploadedAt).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <Card className="h-fit">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Document
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10">
            <FileText className="h-5 w-5 text-primary" />
          </div>
          <div className="min-w-0">
            <p className="font-medium text-sm text-foreground leading-tight break-words">
              {document.name}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {formatFileSize(document.size)}
            </p>
          </div>
        </div>

        <Separator />

        <div className="space-y-2.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5" /> Status
            </span>
            <Badge variant="success">Ready</Badge>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" /> Uploaded
            </span>
            <span className="text-foreground font-medium">{uploadDate}</span>
          </div>
        </div>

        <Separator />

        <Button asChild variant="outline" size="sm" className="w-full gap-2">
          <Link href="/upload">
            <Upload className="h-3.5 w-3.5" />
            New Upload
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}

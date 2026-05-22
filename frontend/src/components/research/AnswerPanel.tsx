import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";

interface AnswerPanelProps {
  answer: string;
  score?: number;
  streaming: boolean;
}

export function AnswerPanel({ answer, score, streaming }: AnswerPanelProps) {
  if (!answer && !streaming) return null;
  const tone = score === undefined ? "default" : score >= 8 ? "success" : score >= 6 ? "warning" : "danger";
  return (
    <Card>
      <CardHeader>
        <CardTitle>Answer</CardTitle>
        {typeof score === "number" && <Badge tone={tone}>Score {score}/10</Badge>}
      </CardHeader>
      <div className="whitespace-pre-wrap text-sm leading-6">
        {answer}
        {streaming && (
          <span className="ml-0.5 inline-block h-4 w-1.5 animate-pulse-dot bg-[var(--primary)] align-text-bottom" />
        )}
      </div>
    </Card>
  );
}

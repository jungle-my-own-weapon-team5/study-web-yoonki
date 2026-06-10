import Image from "next/image";
import { Card, 
  CardHeader, 
  CardDescription, 
  CardContent, 
  CardTitle
} from "@/components/ui/card";

export default function Home() {
  return (
    <div>
      <Card className="max-w-sm">
      <CardHeader>
        <CardTitle>Project Overview</CardTitle>
        <CardDescription>
          Track progress and recent activity for your Next.js app.
        </CardDescription>
      </CardHeader>
      <CardContent>
        Your design system is ready. Start building your next component.
      </CardContent>
    </Card>
    </div>
  );
}

import { useNavigate } from "react-router-dom";
import { Compass } from "lucide-react";
import Button from "../components/common/Button";
import { EmptyState } from "../components/common/StateViews";

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div className="ss-bg ss-grid min-h-screen flex items-center justify-center">
      <EmptyState icon={Compass} title="Page not found" description="The page you are looking for does not exist." action={<Button onClick={() => navigate("/")}>Back to home</Button>} />
    </div>
  );
}
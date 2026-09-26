import { AgentWorkspace } from "@/components/chat/agent-workspace";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { WorkspaceShell } from "@/components/layout/workspace-shell";

export default function AgentsPage() {
    return (
        <ProtectedRoute>
            <WorkspaceShell>
                <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
                    <AgentWorkspace />
                </div>
            </WorkspaceShell>
        </ProtectedRoute>
    );
}
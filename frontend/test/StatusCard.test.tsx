
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import StatusCard from "../components/StatusCard";

describe("StatusCard", () => {
  it("renders badge and chips", () => {
    render(
      <StatusCard
        llmMarkdown="🟢 **Auto-check:** _safe to merge_\n\nrest"
        safe={true}
        summary={{
          checkov_issues: 1,
          policy_fails: 2,
          cost_usd_month: 12.34,
          duration_ms: 456,
        }}
      />
    );

    expect(screen.getByText(/Auto-check/)).toBeInTheDocument();
    expect(screen.getByText("Checkov issues")).toBeInTheDocument();
    expect(screen.getByText("Policy fails")).toBeInTheDocument();
    expect(screen.getByText("$12.34/mo")).toBeInTheDocument();
  });
});

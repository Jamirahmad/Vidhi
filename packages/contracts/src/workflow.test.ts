import { describe, expect, it } from "vitest";

import { workflowCreateResponseSchema, workflowRequestSchema } from "./workflow";

describe("workflowRequestSchema", () => {
  it("applies defaults for optional fields", () => {
    const parsed = workflowRequestSchema.parse({
      caseFacts: {
        title: "Cheque Dishonor Complaint",
        jurisdiction: "IN",
        court: "Metropolitan Magistrate",
        caseType: "criminal",
        facts: "A cheque was issued and returned due to insufficient funds after statutory notice.",
        parties: [{ role: "petitioner", name: "A Kumar" }],
      },
    });

    expect(parsed.preferredLanguage).toBe("en");
    expect(parsed.requireAidSuggestions).toBe(false);
  });

  it("rejects short fact statements", () => {
    const result = workflowRequestSchema.safeParse({
      caseFacts: {
        title: "Short",
        jurisdiction: "IN",
        court: "Court",
        caseType: "civil",
        facts: "too short",
        parties: [{ role: "petitioner", name: "AB" }],
      },
    });

    expect(result.success).toBe(false);
  });
});

describe("workflowCreateResponseSchema", () => {
  it("accepts queued response payload", () => {
    const parsed = workflowCreateResponseSchema.parse({
      jobId: "job-123",
      status: "queued",
    });

    expect(parsed.status).toBe("queued");
  });
});

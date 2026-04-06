import { describe, expect, it } from "vitest";

import { workflowCreateResponseSchema, workflowRequestSchema, workflowStatusSchema } from "./workflow";

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

  it("rejects unknown fields to keep strict request contracts", () => {
    const result = workflowRequestSchema.safeParse({
      caseFacts: {
        title: "Cheque Dishonor Complaint",
        jurisdiction: "IN",
        court: "Metropolitan Magistrate",
        caseType: "criminal",
        facts: "A cheque was issued and returned due to insufficient funds after statutory notice.",
        parties: [{ role: "petitioner", name: "A Kumar" }],
      },
      extra: "not-allowed",
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

describe("workflowStatusSchema", () => {
  it("accepts completed payload with result object", () => {
    const parsed = workflowStatusSchema.parse({
      jobId: "job-123",
      status: "completed",
      result: {
        summary: "Done",
      },
    });

    expect(parsed.status).toBe("completed");
    expect(parsed.progress).toBe(100);
  });

  it("rejects completed payload without result", () => {
    const result = workflowStatusSchema.safeParse({
      jobId: "job-123",
      status: "completed",
    });

    expect(result.success).toBe(false);
  });

  it("rejects failed payload without error", () => {
    const result = workflowStatusSchema.safeParse({
      jobId: "job-123",
      status: "failed",
    });

    expect(result.success).toBe(false);
  });
});

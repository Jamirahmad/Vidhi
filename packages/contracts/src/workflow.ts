import { z } from "zod";

export const caseFactsSchema = z.object({
  title: z.string().min(3),
  jurisdiction: z.string().min(2),
  court: z.string().min(2),
  caseType: z.enum(["civil", "criminal", "tribunal"]),
  facts: z.string().min(20),
  filingDate: z.string().optional(),
  parties: z.array(z.object({ role: z.enum(["petitioner", "respondent"]), name: z.string().min(2) })).min(1),
});

export const workflowRequestSchema = z.object({
  caseFacts: caseFactsSchema,
  preferredLanguage: z.string().default("en"),
  requireAidSuggestions: z.boolean().default(false),
});

export const workflowCreateResponseSchema = z.object({
  jobId: z.string(),
  status: z.literal("queued"),
});

export const workflowStatusSchema = z.object({
  jobId: z.string(),
  status: z.enum(["queued", "running", "completed", "failed"]),
  progress: z.number().int().min(0).max(100).optional(),
  result: z.unknown().optional(),
  error: z.string().nullable().optional(),
});

export type WorkflowRequest = z.input<typeof workflowRequestSchema>;
export type WorkflowCreateResponse = z.infer<typeof workflowCreateResponseSchema>;
export type WorkflowStatusResponse = z.infer<typeof workflowStatusSchema>;

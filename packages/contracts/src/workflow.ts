import { z } from "zod";

const isoDateSchema = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, "Expected date format YYYY-MM-DD");

export const caseFactsSchema = z.object({
  title: z.string().trim().min(3),
  jurisdiction: z.string().trim().min(2),
  court: z.string().trim().min(2),
  caseType: z.enum(["civil", "criminal", "tribunal"]),
  facts: z.string().trim().min(20),
  filingDate: isoDateSchema.optional(),
  parties: z
    .array(
      z
        .object({
          role: z.enum(["petitioner", "respondent"]),
          name: z.string().trim().min(2),
        })
        .strict(),
    )
    .min(1),
}).strict();

export const workflowRequestSchema = z.object({
  caseFacts: caseFactsSchema,
  preferredLanguage: z.enum(["en", "hi"]).default("en"),
  requireAidSuggestions: z.boolean().default(false),
}).strict();

export const workflowCreateResponseSchema = z.object({
  jobId: z.string(),
  status: z.literal("queued"),
}).strict();

const workflowStatusBaseSchema = z.object({
  jobId: z.string(),
});

const queuedStatusSchema = workflowStatusBaseSchema
  .extend({
    status: z.literal("queued"),
    progress: z.number().int().min(0).max(100).default(0),
    result: z.undefined().optional(),
    error: z.undefined().optional(),
  })
  .strict();

const runningStatusSchema = workflowStatusBaseSchema
  .extend({
    status: z.literal("running"),
    progress: z.number().int().min(0).max(100),
    result: z.undefined().optional(),
    error: z.undefined().optional(),
  })
  .strict();

const completedStatusSchema = workflowStatusBaseSchema
  .extend({
    status: z.literal("completed"),
    progress: z.number().int().min(100).max(100).default(100),
    result: z.record(z.string(), z.unknown()),
    error: z.undefined().optional(),
  })
  .strict();

const failedStatusSchema = workflowStatusBaseSchema
  .extend({
    status: z.literal("failed"),
    progress: z.number().int().min(0).max(100).optional(),
    result: z.undefined().optional(),
    error: z.string().min(1),
  })
  .strict();

export const workflowStatusSchema = z.discriminatedUnion("status", [
  queuedStatusSchema,
  runningStatusSchema,
  completedStatusSchema,
  failedStatusSchema,
]);

export type WorkflowRequest = z.input<typeof workflowRequestSchema>;
export type WorkflowCreateResponse = z.infer<typeof workflowCreateResponseSchema>;
export type WorkflowStatusResponse = z.infer<typeof workflowStatusSchema>;

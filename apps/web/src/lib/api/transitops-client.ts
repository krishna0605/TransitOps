import { createTransitOpsClient } from "@transitops/api-client";

import { publicEnv } from "@/config/env";

const baseUrl = publicEnv.NEXT_PUBLIC_API_BASE_URL.replace(/\/api\/v1\/?$/, "");

export const transitOpsClient = createTransitOpsClient({ baseUrl });

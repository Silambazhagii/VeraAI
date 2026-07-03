import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 30000,
    retry: 2,
  });
}

export function useMetadata() {
  return useQuery({
    queryKey: ["metadata"],
    queryFn: api.metadata,
    staleTime: 60000,
  });
}

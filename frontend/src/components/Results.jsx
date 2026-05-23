/*
Expected compare API response shape:

{
  winner: "woolworths" | "coles" | "tie",
  total_woolworths: number,
  total_coles: number,
  savings: number,
  annualised_savings: number,
  breakdown: [
    {
      item: string,
      match_type: "exact" | "branded" | "generic" | "no_match",
      woolworths: {
        name: string,
        brand: string,
        price: number,
        size: string,
        unit_price: number | null,
        unit: string | null,
        on_special: boolean,
        confidence: "high" | "medium" | "low",
      } | null,
      coles: {
        name: string,
        brand: string,
        price: number,
        size: string,
        unit_price: number | null,
        unit: string | null,
        on_special: boolean,
        confidence: "high" | "medium" | "low",
      } | null,
      winner: "woolworths" | "coles" | "tie" | "no_comparison",
      saving: number,
      note: string | null,
    },
  ],
}
*/

export default function Results() {
  return <div>Results</div>;
}

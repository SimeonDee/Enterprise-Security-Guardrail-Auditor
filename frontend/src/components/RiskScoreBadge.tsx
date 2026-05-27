interface Props {
    score: number;
}

export default function RiskScoreBadge({ score }: Props) {
    let color = "bg-green-100 text-green-800";
    if (score >= 70) color = "bg-red-100 text-red-800";
    else if (score >= 40) color = "bg-yellow-100 text-yellow-800";
    else if (score >= 20) color = "bg-orange-100 text-orange-800";

    return (
        <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ${color}`}>
            {score.toFixed(1)}%
        </span>
    );
}

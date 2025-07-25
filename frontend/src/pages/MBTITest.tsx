import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getTest, submitTest, TestTemplate, TestResult } from "../lib/api";

export default function MBTITest() {
  const token = localStorage.getItem("token");
  const navigate = useNavigate();

  if (!token) {
    navigate("/login");
  }

  const { data, isPending, isError } = useQuery({
    queryKey: ["mbti"],
    queryFn: () => getTest(token!, "mbti"),
  });

  const [answers, setAnswers] = useState<number[]>([]);
  const [result, setResult] = useState<TestResult | null>(null);

  const mutation = useMutation({
    mutationFn: (payload: number[]) => submitTest(token!, "mbti", payload),
    onSuccess: (res: { data: TestResult }) => setResult(res.data),
  });

  if (isPending) return <p>Loading…</p>;
  if (isError) return <p>Error loading test.</p>;

  const template: TestTemplate = data!.data;

  function handleChange(qIndex: number, value: number) {
    const newAns = [...answers];
    newAns[qIndex] = value;
    setAnswers(newAns);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (answers.length !== template.questions.length) {
      alert("Please answer all questions");
      return;
    }
    mutation.mutate(answers);
  }

  if (result) {
    return (
      <main style={{ padding: 24 }}>
        <h2>{template.name} – Results</h2>
        <p>{result.interpretation}</p>
        <ul>
          {result.tips.map((t,i)=>(<li key={i}>{t}</li>))}
        </ul>
        <button onClick={() => setResult(null)}>Retake</button>
      </main>
    );
  }

  return (
    <main style={{ padding: 24 }}>
      <h2>{template.name}</h2>
      <p>{template.description}</p>
      <form onSubmit={handleSubmit}>
        {template.questions.map((q, idx) => (
          <div key={q.id} style={{ marginTop: 16 }}>
            <p>{idx + 1}. {q.text}</p>
            {[1,2,3,4,5].map((v) => (
              <label key={v} style={{ marginRight: 8 }}>
                <input
                  type="radio"
                  name={`q-${idx}`}
                  value={v}
                  checked={answers[idx] === v}
                  onChange={() => handleChange(idx, v)}
                /> {v}
              </label>
            ))}
          </div>
        ))}
        <button type="submit" disabled={mutation.isPending} style={{ marginTop: 24 }}>
          Submit
        </button>
      </form>
    </main>
  );
}
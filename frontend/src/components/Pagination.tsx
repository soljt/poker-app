import { Pagination as BPagination } from "react-bootstrap";

export default function Pagination({
  current,
  total,
  onChange,
}: {
  current: number;
  total: number;
  onChange: (newPage: number) => void;
}) {
  const pages = Array.from({ length: total }, (_, i) => i + 1);

  return (
    <BPagination className="mt-4 justify-content-center">
      <BPagination.Prev
        disabled={current === 1}
        onClick={() => onChange(current - 1)}
      />
      {pages.map((page) => (
        <BPagination.Item
          key={page}
          active={page === current}
          onClick={() => onChange(page)}
        >
          {page}
        </BPagination.Item>
      ))}
      <BPagination.Next
        disabled={current === total}
        onClick={() => onChange(current + 1)}
      />
    </BPagination>
  );
}

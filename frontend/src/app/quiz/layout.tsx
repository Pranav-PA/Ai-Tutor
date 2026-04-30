import Sidebar from '@/components/layout/Sidebar';

export default function QuizLayout({ children }: { children: React.ReactNode }) {
  return <Sidebar>{children}</Sidebar>;
}

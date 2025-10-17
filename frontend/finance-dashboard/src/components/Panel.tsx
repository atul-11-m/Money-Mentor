import React, { ReactNode } from "react";

interface PanelProps {
  title: string;
  children?: ReactNode;
}

const Panel: React.FC<PanelProps> = ({ title, children }) => (
  <div className="bg-white shadow rounded-lg p-4 flex flex-col">
    <h2 className="font-semibold mb-2">{title}</h2>
    <div className="flex-1">{children}</div>
  </div>
);

export default Panel;

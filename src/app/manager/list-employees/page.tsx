// src/app/manager/list-employees/page.tsx
"use client";

import { useEffect, useState } from "react";
import { collection, getDocs } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function ListEmployeesPage() {
  const [employees, setEmployees] = useState<any[]>([]);

  useEffect(() => {
    const fetchEmployees = async () => {
      const snapshot = await getDocs(collection(db, "employees"));
      setEmployees(snapshot.docs.map((doc) => doc.data()));
    };
    fetchEmployees();
  }, []);

  return (
    <div className="max-w-3xl mx-auto p-6 mt-10 bg-white shadow-md rounded-lg">
      <h2 className="text-2xl font-bold mb-6 text-center">List of Employees</h2>
      <ul className="space-y-4">
        {employees.map((emp, index) => (
          <li key={index} className="border-b pb-2">
            <p className="font-semibold">{emp.name}</p>
            <p className="text-sm text-gray-500">{emp.email}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

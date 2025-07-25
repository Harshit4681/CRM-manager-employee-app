// src/app/manager/remove-employee/page.tsx
"use client";

import { useState, useEffect } from "react";
import { collection, getDocs, deleteDoc, doc } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function RemoveEmployeePage() {
  const [employees, setEmployees] = useState<any[]>([]);

  useEffect(() => {
    const fetchEmployees = async () => {
      const snapshot = await getDocs(collection(db, "employees"));
      setEmployees(snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() })));
    };
    fetchEmployees();
  }, []);

  const handleDelete = async (id: string) => {
    await deleteDoc(doc(db, "employees", id));
    setEmployees(employees.filter((emp) => emp.id !== id));
  };

  return (
    <div className="max-w-3xl mx-auto p-6 mt-10 bg-white shadow-md rounded-lg">
      <h2 className="text-2xl font-bold mb-6 text-center">Remove Employees</h2>
      <ul className="space-y-4">
        {employees.map((emp) => (
          <li key={emp.id} className="flex justify-between items-center border-b pb-2">
            <div>
              <p className="font-semibold">{emp.name}</p>
              <p className="text-sm text-gray-500">{emp.email}</p>
            </div>
            <button
              className="bg-red-500 text-white px-4 py-1 rounded hover:bg-red-600"
              onClick={() => handleDelete(emp.id)}
            >
              ❌ Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

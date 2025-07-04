import { useCallback, useEffect, useState } from "react";
import UserRow from "../components/UserRow";
import UserForm from "../components/UserForm";
import Pagination from "../components/Pagination";
import { UserRowData } from "../types";
import { admin_api, auth_api, game_api } from "../services/api";
import { Container } from "react-bootstrap";

export default function Admin() {
  const [users, setUsers] = useState<UserRowData[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  function getCookie(name: string) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(";").shift();
  }

  useEffect(() => {
    const refreshCSRF = async () => {
      try {
        // Make a POST to who_am_i to refresh token & get a fresh CSRF cookie
        await auth_api.post("/who_am_i", {});

        // Read the new CSRF cookie
        const csrf = getCookie("csrf_access_token");

        // Update axios instances
        if (csrf !== null) {
          auth_api.defaults.headers.common["X-CSRF-TOKEN"] = csrf;
          game_api.defaults.headers.common["X-CSRF-TOKEN"] = csrf;
          admin_api.defaults.headers.common["X-CSRF-TOKEN"] = csrf;
        }
      } catch (err) {
        console.error("Failed to refresh CSRF token:", err);
      }
    };

    refreshCSRF();
  }, []);

  const fetchUsers = useCallback(() => {
    admin_api.get(`users?page=${page}`).then((res) => {
      const data = res.data;
      setUsers(data.users);
      setTotalPages(data.totalPages);
    });
  }, [page]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return (
    <Container>
      <div className="container my-4">
        <h2 className="text-center mb-4">Admin Dashboard</h2>
      </div>

      <UserForm onUserCreated={fetchUsers} />

      {users.map((u) => (
        <UserRow key={u.id} user={u} onChange={fetchUsers} />
      ))}

      <Pagination current={page} total={totalPages} onChange={setPage} />
    </Container>
  );
}

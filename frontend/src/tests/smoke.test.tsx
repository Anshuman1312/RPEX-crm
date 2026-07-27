import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Provider } from "react-redux";
import { store } from "@/app/store";
import { LoginPage } from "@/features/auth/pages/LoginPage";

describe("Login page", () => {
  it("renders sign in heading", () => {
    render(
      <Provider store={store}>
        <MemoryRouter>
          <LoginPage />
        </MemoryRouter>
      </Provider>
    );

    expect(screen.getByText("Sign in to RPEX CRM")).toBeInTheDocument();
  });
});

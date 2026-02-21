package main

import "github.com/gofiber/fiber/v3"

func main() {
	app := fiber.New()

	app.Get("/health", healthHandler)
	app.Post("/api/balance", balanceHandler)
	app.Get("", func(c fiber.Ctx) error {
		return c.SendFile("./index.html")
	})

	app.Listen(":3000")
}

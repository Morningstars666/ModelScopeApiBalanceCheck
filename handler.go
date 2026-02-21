package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/gofiber/fiber/v3"
)

type BalanceRequest struct {
	Models []string `json:"models"`
	ApiKey string   `json:"api_key"`
}

type BalanceItem struct {
	Model                 string  `json:"model"`
	RequestLimit          int     `json:"request_limit"`
	RequestRemaining      int     `json:"request_remaining"`
	ModelRequestLimit     int     `json:"model_request_limit"`
	ModelRequestRemaining int     `json:"model_request_remaining"`
	Error                 *string `json:"error"`
}

type BalanceResponse struct {
	Success bool          `json:"success"`
	Data    []BalanceItem `json:"data"`
	Message string        `json:"message"`
}

func healthHandler(c fiber.Ctx) error {
	return c.JSON(fiber.Map{
		"status":  "healthy",
		"service": "ModelScope Balance Query",
	})
}

func balanceHandler(c fiber.Ctx) error {
	var req = new(BalanceRequest)
	if err := c.Bind().Body(req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"success": false,
			"message": "请求体解析失败",
			"error":   err.Error(),
		})
	}

	apiKey := strings.TrimSpace(req.ApiKey)
	if len(req.Models) == 0 || apiKey == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"success": false,
			"message": "models或api_key不能为空",
		})
	}

	client := &http.Client{Timeout: 30 * time.Second}
	results := make([]BalanceItem, 0, len(req.Models))
	successCount := 0

	for _, model := range req.Models {
		trimmedModel := strings.TrimSpace(model)
		item := BalanceItem{Model: trimmedModel}
		if trimmedModel == "" {
			errMsg := "model不能为空"
			item.Error = &errMsg
			results = append(results, item)
			continue
		}
		if err := queryModelScopeBalance(client, trimmedModel, apiKey, &item); err != nil {
			errMsg := err.Error()
			item.Error = &errMsg
		} else {
			successCount++
		}
		results = append(results, item)
	}

	success := successCount == len(results)
	message := fmt.Sprintf("成功查询 %d 个模型的余额信息", successCount)
	if !success {
		message = fmt.Sprintf("成功查询 %d 个模型的余额信息，失败 %d 个模型", successCount, len(results)-successCount)
	}

	return c.JSON(BalanceResponse{
		Success: success,
		Data:    results,
		Message: message,
	})
}

func queryModelScopeBalance(client *http.Client, model, apiKey string, item *BalanceItem) error {
	payload := map[string]interface{}{
		"model":           model,
		"messages":        []map[string]string{{"role": "user", "content": "返回一个好字"}},
		"stream":          false,
		"enable_thinking": false,
		"system_prompt":   "",
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	request, err := http.NewRequest("POST", "https://api-inference.modelscope.cn/v1/chat/completions", bytes.NewReader(body))
	if err != nil {
		return err
	}
	request.Header.Set("Authorization", "Bearer "+apiKey)
	request.Header.Set("Content-Type", "application/json")

	response, err := client.Do(request)
	if err != nil {
		return err
	}
	defer response.Body.Close()

	if response.StatusCode < http.StatusOK || response.StatusCode >= http.StatusMultipleChoices {
		bodyBytes, _ := io.ReadAll(response.Body)
		if len(bodyBytes) == 0 {
			return fmt.Errorf("请求失败，状态码 %d", response.StatusCode)
		}
		return fmt.Errorf("请求失败，状态码 %d: %s", response.StatusCode, strings.TrimSpace(string(bodyBytes)))
	}

	item.RequestLimit = parseHeaderInt(response.Header.Get("modelscope-ratelimit-requests-limit"))
	item.RequestRemaining = parseHeaderInt(response.Header.Get("modelscope-ratelimit-requests-remaining"))
	item.ModelRequestLimit = parseHeaderInt(response.Header.Get("modelscope-ratelimit-model-requests-limit"))
	item.ModelRequestRemaining = parseHeaderInt(response.Header.Get("modelscope-ratelimit-model-requests-remaining"))

	_, _ = io.Copy(io.Discard, response.Body)
	return nil
}

func parseHeaderInt(value string) int {
	trimmed := strings.TrimSpace(value)
	if trimmed == "" {
		return 0
	}
	parsed, err := strconv.Atoi(trimmed)
	if err != nil {
		return 0
	}
	return parsed
}

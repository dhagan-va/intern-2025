package client

import "go-port/config"

type LoadClient struct {
	RPS      float64
	Running  bool
	Endpoint string
}

func Init(cfg *config.Config) *LoadClient {
	return &LoadClient{
		RPS:      cfg.RPS,
		Running:  false,
		Endpoint: cfg.Endpoint,
	}
}

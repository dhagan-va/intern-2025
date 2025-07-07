package config

type Config struct {
	Endpoint string
	RPS      float64
	Threads  int
}

func Load(path string) (*Config, error) {
	cfg := Config{Endpoint: "http://127.0.0.1:5000/270/", RPS: 2, Threads: 2}
	return &cfg, nil
}

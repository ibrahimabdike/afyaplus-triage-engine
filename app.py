# app.py - AfyaPlus Triage Engine (with fixed local timeout)
import os
import json
import time
from typing import Dict, Tuple
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

class AfyaPlusTriage:
    """Main triage engine with cloud/local fallback"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found")
        
        # Cloud client
        self.cloud = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            timeout=4.0
        )
        
        # Local client - check Ollama
        self.local = None
        self.local_available = False
        self.local_model = "llama3.2"
        
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=2.0)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    self.local_model = models[0]['name']
                    print(f"Local Ollama available with model: {self.local_model}")
                    
                    # Initialize with longer timeout for local
                    self.local = OpenAI(
                        base_url="http://localhost:11434/v1",
                        api_key="ollama",
                        timeout=60.0  # 60 seconds for local models
                    )
                    self.local_available = True
                else:
                    print("No models found. Run: ollama pull llama3.2")
            else:
                print("Ollama not responding")
        except Exception as e:
            print(f"Local Ollama not available: {e}")
    
    def _prompt_v3(self, msg: str) -> str:
        return f"""
        Defensive triage system for AfyaPlus Health.
        RULES: No diagnoses, no prescriptions, no fluff. Conservative.
        Patient: {msg}
        Return ONLY JSON:
        {{
          "is_critical_emergency": boolean,
          "detected_symptoms": ["string"],
          "clinical_reasoning_summary": "string",
          "routing_destination": "Emergency Room | Clinic Appointment | Home Care"
        }}
        """
    
    def _call_cloud(self, prompt: str) -> Tuple[str, float, bool]:
        """Call cloud model"""
        start = time.time()
        try:
            response = self.cloud.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Process this message."}
                ],
                temperature=0.0,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content, time.time() - start, True
        except Exception as e:
            return f"ERROR: {e}", time.time() - start, False
    
    def _call_local(self, prompt: str) -> Tuple[str, float, bool]:
        """Call local model with longer timeout"""
        if not self.local_available or not self.local:
            return "Local not available", 0.0, False
        
        start = time.time()
        try:
            print("(this may take up to 60 seconds)...", end=" ", flush=True)
            response = self.local.chat.completions.create(
                model=self.local_model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Process this message."}
                ],
                temperature=0.0,
                max_tokens=300
            )
            elapsed = time.time() - start
            return response.choices[0].message.content, elapsed, True
        except Exception as e:
            elapsed = time.time() - start
            print(f"Local error: {e}")
            return f"ERROR: {e}", elapsed, False
    
    def _parse_json(self, text: str) -> Dict:
        """Safe JSON parsing"""
        cleaned = text.strip()
        for prefix in ['```json', '```']:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        data = json.loads(cleaned.strip())
        required = ["is_critical_emergency", "detected_symptoms", 
                   "clinical_reasoning_summary", "routing_destination"]
        for key in required:
            if key not in data:
                raise ValueError(f"Missing key: {key}")
        return data
    
    def triage(self, message: str) -> Tuple[Dict, str, float]:
        """Main triage with timing"""
        prompt = self._prompt_v3(message)
        
        # Try cloud first
        print("Cloud...", end=" ", flush=True)
        response, elapsed, success = self._call_cloud(prompt)
        
        if success:
            print(f"OK ({elapsed:.2f}s)")
            return self._parse_json(response), "cloud", elapsed
        else:
            print(f"FAILED ({elapsed:.2f}s)")
            return self._fallback(message)
    
    def _fallback(self, message: str) -> Tuple[Dict, str, float]:
        """Local fallback"""
        prompt = self._prompt_v3(message)
        
        if self.local_available:
            print("Local...", end=" ", flush=True)
            response, elapsed, success = self._call_local(prompt)
            
            if success:
                print(f"OK ({elapsed:.2f}s)")
                try:
                    return self._parse_json(response), "local", elapsed
                except Exception as e:
                    print(f"Parse error: {e}")
            else:
                print(f"FAILED ({elapsed:.2f}s)")
        
        # Emergency default
        print("Using emergency default")
        return {
            "is_critical_emergency": True,
            "detected_symptoms": ["system_error"],
            "clinical_reasoning_summary": "Unable to process - human review",
            "routing_destination": "Human Review"
        }, "error", 0.0
    
    def run(self, message: str = None) -> Dict:
        """Single message processing"""
        if not message:
            message = "I'm 7 months pregnant with severe headache and swollen feet"
        
        print("\n" + "="*70)
        print(f"PATIENT: {message}")
        print("="*70)
        
        result, source, elapsed = self.triage(message)
        
        print("\nRESULTS:")
        print("-" * 50)
        print(f"EMERGENCY: {'YES' if result['is_critical_emergency'] else 'NO'}")
        print(f"SYMPTOMS: {', '.join(result['detected_symptoms'])}")
        print(f"REASONING: {result['clinical_reasoning_summary']}")
        print(f"ROUTE: {result['routing_destination']}")
        print(f"SOURCE: {source.upper()}")
        print(f"TIME: {elapsed:.2f}s")
        
        action = "IMMEDIATE EMERGENCY ROUTING" if result['is_critical_emergency'] else "Standard clinic routing"
        print(f"\nACTION: {action}")
        print("="*70 + "\n")
        
        return result
    
    def benchmark(self):
        """Performance comparison with detailed timing"""
        print("\n" + "="*70)
        print("BENCHMARK")
        print("="*70)
        
        tests = [
            "Mild headache and fever",
            "Severe chest pain, difficulty breathing",
            "Child with rash and fever"
        ]
        
        results = []
        for msg in tests:
            print(f"\nTesting: {msg}")
            
            prompt = self._prompt_v3(msg)
            
            # Cloud test
            print("  Cloud...", end=" ", flush=True)
            start = time.time()
            _, c_time, c_ok = self._call_cloud(prompt)
            print(f"{c_time:.2f}s {'OK' if c_ok else 'FAILED'}")
            
            # Local test
            print("  Local...", end=" ", flush=True)
            start = time.time()
            _, l_time, l_ok = self._call_local(prompt)
            print(f"{l_time:.2f}s {'OK' if l_ok else 'FAILED'}")
            
            results.append((msg[:20], c_time if c_ok else None, 
                          l_time if l_ok else None, c_ok, l_ok))
        
        print("\nPERFORMANCE:")
        print("-" * 70)
        print(f"{'Message':<25} {'Cloud (s)':<12} {'Local (s)':<12} {'Speedup':<12}")
        print("-" * 70)
        
        cloud_times = []
        local_times = []
        
        for msg, c, l, c_ok, l_ok in results:
            c_str = f"{c:.2f}" if c_ok else "Failed"
            l_str = f"{l:.2f}" if l_ok else "Failed"
            
            speedup = "N/A"
            if c_ok and l_ok and c > 0:
                speedup = f"{l/c:.1f}x"
                cloud_times.append(c)
                local_times.append(l)
            
            print(f"{msg:<25} {c_str:<12} {l_str:<12} {speedup:<12}")
        
        # Summary statistics
        if cloud_times and local_times:
            print("-" * 70)
            print("SUMMARY:")
            print(f"  Cloud average: {sum(cloud_times)/len(cloud_times):.2f}s")
            print(f"  Local average: {sum(local_times)/len(local_times):.2f}s")
            print(f"  Cloud is {sum(local_times)/sum(cloud_times):.1f}x faster")
            print(f"  Success rate: Cloud {len([r for r in results if r[3]])}/{len(results)}, "
                  f"Local {len([r for r in results if r[4]])}/{len(results)}")
        
        if not any(l_ok for _, _, _, _, l_ok in results):
            print("\nLocal Ollama not working. Possible fixes:")
            print("  1. Check if model exists: ollama list")
            print("  2. Pull a model: ollama pull llama3.2")
            print("  3. Try a smaller model: ollama pull mistral")
            print("  4. Update code to use: model='mistral'")
            print("  5. Check if Ollama is running: ollama ps")

def main():
    """CLI entry point"""
    import sys
    
    print("AFYAPLUS TRIAGE ENGINE")
    print("="*70)
    
    engine = AfyaPlusTriage()
    
    # Parse command line
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
        engine.run(msg)
    else:
        engine.run()
    
    # Run benchmark
    engine.benchmark()
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
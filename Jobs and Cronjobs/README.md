# 🚀 Kubernetes Jobs: One-Time Tasks to Completion

<img src="https://github.com/bhuvan-raj/Kubernetes-EKS-FROM-SCRATCH/blob/main/Jobs%20and%20Cronjobs/assets/jobs.png" alt="Banner" />


A **Kubernetes Job** is a controller that creates one or more Pods and ensures that a specified number of them successfully complete their tasks. Unlike a Deployment, which aims to keep a set of Pods running continuously, a Job's primary purpose is to run a task to completion and then terminate.



### How Jobs Work

When you create a Job, Kubernetes launches one or more Pods. These Pods execute the defined task. If a Pod fails or is terminated for any reason (e.g., node failure), the Job controller will automatically create a new Pod to replace it, ensuring the task eventually finishes. The Job is considered complete when the specified number of successful Pod completions is met.

### Key Characteristics of Jobs

* **Finite Tasks:** Jobs are designed for tasks that have a definite end.
* **Completion Tracking:** Jobs track the successful completion of Pods.
* **Automatic Retries:** If a Pod fails, the Job automatically retries it (up to a configurable `backoffLimit`).
* **Parallelism:** Jobs can be configured to run multiple Pods in parallel, either to complete a fixed number of tasks or to process items from a work queue.
* **Restart Policy:** Pods created by a Job must have a `restartPolicy` of `OnFailure` or `Never`. `Always` is not allowed because a Job is meant to terminate.

### Use Cases for Jobs

Jobs are ideal for:

* **Batch Processing:** Processing a large dataset in chunks.
* **Data Migrations:** Running a script to update a database schema or migrate data.
* **One-time Cleanup Tasks:** Deleting old files or rotating logs.
* **Report Generation:** Generating a periodic report.
* **Computational Tasks:** Running complex calculations that have a defined endpoint.

### Example Kubernetes Job Definition (YAML)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi-calculator-job
spec:
  template:
    spec:
      containers:
      - name: pi-calculator
        image: perl
        command: ["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: OnFailure
  completions: 1  # Number of times the Job should run to completion
  backoffLimit: 4 # Number of retries before marking the Job as failed
````

-----

## ⏰ Kubernetes CronJobs: Scheduled Recurring Tasks

<img src="https://github.com/bhuvan-raj/Kubernetes-EKS-FROM-SCRATCH/blob/main/Jobs%20and%20Cronjobs/assets/cronjobs.png" alt="Banner" />


A **Kubernetes CronJob** automates the creation of Jobs on a repeating schedule. It's akin to the `cron` utility found in Unix-like operating systems but integrated into Kubernetes, allowing you to schedule routine tasks within your cluster.

### How CronJobs Work

A CronJob object defines a schedule using the standard `cron` format. At each scheduled interval, the CronJob controller creates a new Job object. This Job then functions exactly like a standalone Job, creating Pods to execute the defined task, ensuring completion, and handling retries.

### Key Characteristics of CronJobs

  * **Scheduled Execution:** Runs tasks at specified times or intervals using `cron` syntax.
  * **Job Template:** Each CronJob contains a `jobTemplate` that specifies the details of the Job to be created.
  * **Concurrency Policy:** Defines how to handle concurrent Job executions if a previous Job is still running when a new one is scheduled. Options are:
      * `Allow` (default): Allows concurrent Jobs.
      * `Forbid`: Skips the new Job if a previous one is still running.
      * `Replace`: Terminates the existing Job and replaces it with the new one.
  * **History Limits:** You can configure how many successful (`successfulJobsHistoryLimit`) and failed (`failedJobsHistoryLimit`) Jobs are kept in the history for auditing and debugging.
  * **Starting Deadline:** `startingDeadlineSeconds` can be set to specify a deadline (in seconds) for a Job to start if it misses its scheduled time. If the deadline is passed, the Job won't be created for that schedule.

### Cron Syntax Refresher

The `cron` schedule string consists of five fields representing:

```
minute hour day-of-month month day-of-week
```

Each field can contain:

  * `*`: Wildcard, matches any value.
  * `,`: List separator (e.g., `1,3,5` for minutes 1, 3, and 5).
  * `-`: Range (e.g., `9-17` for hours 9 through 17).
  * `/`: Step values (e.g., `*/5` for every 5th minute).

**Examples:**

  * `0 0 * * *`: Run daily at midnight.
  * `*/5 * * * *`: Run every 5 minutes.
  * `0 8 * * 1-5`: Run every weekday at 8 AM.

### Use Cases for CronJobs

CronJobs are perfect for:

  * **Scheduled Backups:** Regularly backing up databases or file systems.
  * **Periodic Data Synchronization:** Syncing data between different systems.
  * **Log Rotation/Cleanup:** Deleting old logs or cleaning up temporary files.
  * **Reporting:** Generating daily, weekly, or monthly reports.
  * **System Maintenance:** Running health checks or database optimization scripts at off-peak hours.

### Example Kubernetes CronJob Definition (YAML)

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-backup
spec:
  schedule: "0 2 * * *" # Run daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup-script
            image: my-custom-backup-image:latest
            command: ["/bin/sh", "-c", "mysqldump -u root -p$MYSQL_ROOT_PASSWORD --all-databases > /backups/all-databases-$(date +%Y%m%d).sql"]
            env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-credentials
                  key: password
          restartPolicy: OnFailure
  concurrencyPolicy: Forbid # Do not run a new Job if the previous one is still running
  successfulJobsHistoryLimit: 3 # Keep history of last 3 successful Jobs
  failedJobsHistoryLimit: 1 # Keep history of last 1 failed Job
```

-----

## 🛠️ Managing Jobs and CronJobs

You can interact with Jobs and CronJobs using `kubectl` commands:

  * **To create a Job/CronJob:**
    ```bash
    kubectl apply -f your-job-or-cronjob.yaml
    ```
  * **To list Jobs:**
    ```bash
    kubectl get jobs
    ```
  * **To list CronJobs:**
    ```bash
    kubectl get cronjobs
    ```
  * **To get detailed information about a Job/CronJob:**
    ```bash
    kubectl describe job <job-name>
    kubectl describe cronjob <cronjob-name>
    ```
  * **To view logs of a Pod created by a Job:**
    First, find the Pod name:
    ```bash
    kubectl get pods -l job-name=<job-name>
    ```
    Then, view logs:
    ```bash
    kubectl logs <pod-name>
    ```
  * **To delete a Job/CronJob:**
    ```bash
    kubectl delete job <job-name>
    kubectl delete cronjob <cronjob-name>
    ```
    Deleting a Job will also delete the Pods it created.

-----

## ⚖️ Key Differences and When to Use Which

| Feature               | Kubernetes Job                                 | Kubernetes CronJob                                   |
| :-------------------- | :--------------------------------------------- | :--------------------------------------------------- |
| **Purpose** | Run a one-time, finite task to completion.     | Schedule recurring tasks at defined intervals.       |
| **Trigger** | Manually created, or created by a CronJob.     | Time-based schedule (cron syntax).                   |
| **Lifecycle** | Runs until completion, then terminates.        | Continuously creates new Jobs based on the schedule. |
| **Concurrency** | Can run multiple Pods in parallel for a single task. | Manages concurrency of its created Jobs.             |
| **Use Cases** | Data migrations, one-off reports, batch processing. | Backups, log rotation, periodic data sync, scheduled maintenance. |

**In essence:**

  * Use a **Job** when you need a task to run once and ensure it completes successfully, even if Pods fail.
  * Use a **CronJob** when you need a task to run repeatedly on a specific schedule. The CronJob will create Jobs for each scheduled execution.

<!-- end list -->

```
```

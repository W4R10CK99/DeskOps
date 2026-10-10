export type TaskStatus = 'In progress' | 'To do' | 'Review' | 'Done';

export type Task = {
  id: string;
  title: string;
  owner: string;
  due: string;
  status: TaskStatus;
};

export type Project = {
  id: string;
  name: string;
  customer: string;
  description: string;
  color: string;
  tasks: Task[];
};

export const initialProjects: Project[] = [
  {
    id: 'northstar',
    name: 'Northstar onboarding',
    customer: 'Northstar Health',
    description: 'A smooth launch for the customer success team and their regional clinics.',
    color: 'violet',
    tasks: [
      {
        id: 'task-101',
        title: 'Confirm workspace requirements',
        owner: 'Maya Chen',
        due: 'Oct 14',
        status: 'In progress',
      },
      {
        id: 'task-102',
        title: 'Prepare clinic import template',
        owner: 'Jordan Lee',
        due: 'Oct 16',
        status: 'To do',
      },
      {
        id: 'task-103',
        title: 'Review launch checklist',
        owner: 'Sam Rivera',
        due: 'Oct 18',
        status: 'Review',
      },
    ],
  },
  {
    id: 'meridian',
    name: 'Meridian Q4 rollout',
    customer: 'Meridian Labs',
    description: 'Coordinate the Q4 rollout across operations, support, and product.',
    color: 'blue',
    tasks: [
      {
        id: 'task-201',
        title: 'Map support handoff',
        owner: 'Jordan Lee',
        due: 'Oct 12',
        status: 'Done',
      },
      {
        id: 'task-202',
        title: 'Share rollout timeline',
        owner: 'Maya Chen',
        due: 'Oct 20',
        status: 'In progress',
      },
    ],
  },
  {
    id: 'atlas',
    name: 'Atlas renewal review',
    customer: 'Atlas Group',
    description: 'Gather delivery notes and prepare a clear renewal review.',
    color: 'green',
    tasks: [],
  },
];

export const teamMembers = ['Maya Chen', 'Jordan Lee', 'Sam Rivera', 'Alex Morgan'];

export const sampleDocuments = [
  {
    id: 'doc-1',
    name: 'Northstar launch checklist.pdf',
    project: 'Northstar onboarding',
    type: 'PDF',
    updated: 'Today',
    size: '1.2 MB',
  },
  {
    id: 'doc-2',
    name: 'Meridian rollout plan.docx',
    project: 'Meridian Q4 rollout',
    type: 'DOC',
    updated: 'Yesterday',
    size: '846 KB',
  },
  {
    id: 'doc-3',
    name: 'Customer handoff notes.pdf',
    project: 'Northstar onboarding',
    type: 'PDF',
    updated: 'Oct 7',
    size: '392 KB',
  },
  {
    id: 'doc-4',
    name: 'Atlas renewal brief.pdf',
    project: 'Atlas renewal review',
    type: 'PDF',
    updated: 'Oct 4',
    size: '2.1 MB',
  },
];
